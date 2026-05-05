function detectFaction(userAgent) {
  if (!userAgent) return 'spectator';
  const ua = userAgent.toLowerCase();

  const isIOS = /ipad|iphone|ipod/.test(ua);
  const isMacTouch = /macintosh/.test(ua) && /mobile/.test(ua);
  const isAndroid = /android/.test(ua);

  if (isIOS || isMacTouch) return 'orchard';
  if (isAndroid) return 'jungle';
  return 'spectator';
}

module.exports = { detectFaction };
