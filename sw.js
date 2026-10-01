// 천타버스 서비스 워커 — 휴대폰 알림 전용(2026-10-01). index.html의 swNotify 곁 주석.
// 휴대폰 브라우저는 페이지의 new Notification을 거부해, 알림을 띄우려면 서비스 워커 등록이 있어야 한다. 그 등록만을 위한 파일이다.
// fetch를 가로채지 않는다 — 캐시·오프라인 동작을 만들지 않는다(사이트 새 판 확인·10초 갱신에 끼어들지 않게). 넣지 말 것.
// 알림을 누르면: 열려 있는 사이트 창을 앞으로 가져오고 'notify-click'을 보낸다(페이지가 최근 활동으로 옮긴다). 창이 없으면 최근 활동으로 새로 연다.
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil((async () => {
    const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    if (list.length) { list[0].postMessage('notify-click'); return list[0].focus(); }
    return self.clients.openWindow('./#recent');
  })());
});
