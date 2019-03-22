# coding: utf8 
"""  
"""
import os
import signal
import time
import json
import copy
import argparse
import asyncio
import psutil
import pyppeteer
import tornado.ioloop
import tornado.web
import requests
from pyobject import PyObject


class BrowserContext(PyObject):
    def __init__(self):
        PyObject.__init__(self)
        self.name = ''
        self.browser = None
        self.connected = None
        self.DEFAULT_UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS '
                '11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, '
                'like Gecko) Version/11.0 Mobile/15A372 Safari/604.1')
        self.deadline = 0


    async def recheck(self):
        pages = await self.browser.pages()
        if len(pages) == 1 and pages[0].url == 'about:blank':
            self.deadline = 0


    async def get_browser(self):
        if not self.browser or not self.connected:
            await self.reset()
            return None
        if self.deadline:
            if self.deadline < time.time():
                await self.reset()
            return None
        pages = await self.browser.pages()
        self.log.info('[{}] current pages'.format(self.name))
        for idx,p in enumerate(pages):
            self.log.info('\t[{}:{}:{}]'.format(idx, p.isClosed(), p.url))
        if len(pages) == 1 and pages[0].url == 'about:blank':
            return self.browser
        await self.reset()
        return None


    async def reset(self):
        self.log.info('reset')
        if self.browser:
            self.suicide()
            #await self.close_browser()
        while not self.connected:
            await self.launch_browser()
        

    async def launch_browser(self):
        self.log.info('launch browser')
        self.browser = await pyppeteer.launch(args=['--no-sandbox'], 
                ignoreHTTPSErrors=True, handleSIGHUP=False, autoClose=False)
        self.log.info('browser launched on [{}][{}]'.format(
                self.browser.process.pid, self.browser.wsEndpoint))
        self.name = str(self.browser.process.pid)
        self.connected = True
        self.deadline = 0

    
    def on_disconnected(self):
        self.log.warning('Disconnected')
        self.connected = False


    async def close_browser(self):
        self.log.info('close current browser [{}][{}]'.format(
                self.browser.process.pid, self.browser.wsEndpoint))
        await self.browser.close()
        self.name = ''
        self.browser = None
        self.connected = False
        self.deadline = 0


    def suicide(self):
        sig = signal.SIGTERM
        pid = self.browser.process.pid
        self.log.info('suicide [{}]'.format(pid))
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for c in children:
                c.send_signal(sig)
            parent.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
        self.name = ''
        self.browser = None
        self.connected = False
        self.deadline = 0


class BrowserPool(PyObject):
    def __init__(self, pool_size=5):
        PyObject.__init__(self)
        self.pool = [BrowserContext() for i in range(pool_size)]


    async def get_browser_context(self, deadline):
        self.log.info('get browser context')
        for ctx in self.pool:
            self.log.info('check [{}]'.format(ctx.name))
            browser = await ctx.get_browser()
            if browser is not None:
                self.log.info('get [{}]'.format(ctx.name))
                ctx.daedline = deadline
                return ctx
        return None
    

DEFAULT_UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS '
        '11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, '
        'like Gecko) Version/11.0 Mobile/15A372 Safari/604.1')
g_pool = BrowserPool()


class OpenRequestHandler(PyObject, tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        PyObject.__init__(self)
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)


    def fail(self, code, desc='', html=''):
        self.write({'status': 'FAILED', 'error_code': str(code), 
                'error_desc': str(desc), 'html': html})
        self.flush()


    async def run_coroutine(self, c, timeout=5, fail_value=None):
        task = asyncio.create_task(c)
        done, pending = await asyncio.wait({task}, timeout=timeout)
        if pending:
            task.cancel()
            return fail_value
        return list(done)[0].result()


    async def post(self):
        self.log.info('receiv POST request')
        url = self.get_argument('url', default='')
        ua = self.get_argument('user-agency', default=DEFAULT_UA)
        timeout = float(self.get_argument('timeout', default=5))
        actions = self.get_argument('actions', '[]')
        actions = json.loads(actions)
        
        try:
            ctx = await self.run_coroutine(
                    g_pool.get_browser_context(time.time() + timeout), timeout)
            if ctx == None:
                self.log.error('get browser failed')
                return self.fail('GET_BROWSER_FAILED')

            self.log.info('new page [{}]'.format(url))
            page = await self.run_coroutine(ctx.browser.newPage(), timeout)
            if page == None:
                self.log.error('new page failed')
                return self.fail('NEW_PAGE_FAILED')

            r = await self.run_coroutine(page.setUserAgent(ua), timeout, -1)
            if r == -1:
                self.log.error('set ua failed')
                return self.fail('SET_UA_FAILED')
            
            r = await self.run_coroutine(page.goto(url), timeout, -1)
            if r == -1:
                self.log.error('goto url failed')
                return self.fail('GOTO_URL_FAILED')
                
            idx = await self.do_actions(page, actions, timeout)
            html = await self.run_coroutine(page.content(), timeout)
            if html == None:
                self.log.error('get content failed')
                return self.fail('GET_CONTENT_FAILED')

            await self.run_coroutine(page.close(), timeout)
            await self.run_coroutine(ctx.recheck(), timeout)
            self.write({'status': 'OK', 'index': idx, 'html': html})
            self.flush()
        except Exception as e:
            self.log.exception(e)
            self.fail('SERVICE_EXCEPTION', e)

    
    async def do_actions(self, page, actions, timeout):
        for idx,act in enumerate(actions):
            method = act[0]
            args = act[1] if len(act) > 1 else ()
            kwargs = act[2] if len(act) > 2 else {}
            self.log.info('action [{}:{}:{}]'.format(method, args, kwargs))
            root = page
            for r in method.split('.'):
                func = getattr(root, r)
                root = func
            done, pending = await asyncio.wait({func(*args, **kwargs)}, 
                    timeout=timeout)
            if pending:
                self.log.warning('action failed')
                return idx
        return len(actions)


class BrowserAgencyService(tornado.web.Application):
    def __init__(self):
        handlers = [
                (r"/_open", OpenRequestHandler)
        ]   
        settings = dict(
            debug=True,
        )   
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="specify port", 
            default=8005, type=int)
    args = parser.parse_args()
    service = tornado.httpserver.HTTPServer(BrowserAgencyService())
    service.listen(args.port)
    print('service listen on [{}]'.format(args.port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

