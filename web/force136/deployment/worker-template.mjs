const APP=/*__APP__*/;
const HOME=/*__HOME__*/;
const PRINTABLES=/*__PRINTABLES__*/;
const PDFS=/*__PDFS__*/;
export default {
 async fetch(request, env) {
  const p=new URL(request.url).pathname;
  const base={'Cache-Control':'public, max-age=0, must-revalidate','X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin'};
  if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers:{Allow:'GET, HEAD'}});
  if(p==='/'||p==='/index.html')return new Response(request.method==='HEAD'?null:HOME,{headers:{...base,'Content-Type':'text/html; charset=utf-8'}});
  if(p==='/games/force136')return Response.redirect(new URL('/games/force136/',request.url).href,308);
  if(p==='/games/force136/printables')return Response.redirect(new URL('/games/force136/printables/',request.url).href,308);
  if(['/games/force136/printables/','/games/force136/printables/index.html'].includes(p))return new Response(request.method==='HEAD'?null:PRINTABLES,{headers:{...base,'Content-Type':'text/html; charset=utf-8'}});
  if(['/games/force136/','/games/force136/index.html','/games/force136/Force_136_Digital_Deck.html','/downloads/force136'].includes(p)){
   const headers={...base,'Content-Type':'text/html; charset=utf-8'};
   if(p.endsWith('Force_136_Digital_Deck.html')||p==='/downloads/force136')headers['Content-Disposition']='attachment; filename="Force_136_Digital_Deck.html"';
   return new Response(request.method==='HEAD'?null:APP,{headers});
  }
  if(PDFS[p])return new Response(request.method==='HEAD'?null:Uint8Array.from(atob(PDFS[p]),c=>c.charCodeAt(0)),{headers:{...base,'Content-Type':'application/pdf'}});
  if(p.startsWith('/games/force136/'))return new Response('Not found',{status:404});
  return env.ASSETS.fetch(request);
 }
};
