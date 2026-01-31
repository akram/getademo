(() => {
  const log = (...args) => console.log('[demo]', ...args);

  const q = (sel) => document.querySelector(sel);
  const qa = (sel) => Array.from(document.querySelectorAll(sel));

  const setValue = (sel, value) => {
    const el = q(sel);
    if (!el) return false;
    el.focus();
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  };

  const clickSel = (sel) => {
    const el = q(sel);
    if (!el) return false;
    el.click();
    return true;
  };

  const clickNext = () => {
    // Common IDs in the Google signup flow
    if (clickSel('#accountDetailsNext')) return true;
    if (clickSel('#personalDetailsNext')) return true;
    if (clickSel('#next')) return true;

    // Fallback: any visible button labeled "Next"
    const btn = qa('button')
      .filter((b) => b && b.offsetParent !== null)
      .find((b) => (b.innerText || '').trim().toLowerCase() === 'next');
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  };

  const waitFor = (predicate, timeoutMs = 20000, pollMs = 250) =>
    new Promise((resolve, reject) => {
      const start = Date.now();
      const t = setInterval(() => {
        try {
          if (predicate()) {
            clearInterval(t);
            resolve(true);
            return;
          }
          if (Date.now() - start > timeoutMs) {
            clearInterval(t);
            reject(new Error('timeout'));
          }
        } catch (e) {
          clearInterval(t);
          reject(e);
        }
      }, pollMs);
    });

  const ts = String(Date.now()).slice(-6);
  const username = `redhat.demo.${ts}`;
  const password = 'DemoPassw0rd!';

  const run = async () => {
    log('Starting demo autofill...');

    // Step 1: account details
    try {
      await waitFor(() => q('input[name="firstName"]'));
      setValue('input[name="firstName"]', 'Demo');
      setValue('input[name="lastName"]', 'User');
      setValue('input[name="Username"]', username);
      setValue('input[name="Passwd"]', password);
      setValue('input[name="ConfirmPasswd"]', password);
      log('Filled name/username/password');

      setTimeout(() => {
        log('Clicking Next');
        clickNext();
      }, 1200);
    } catch (e) {
      log('Could not find initial form fields (page layout may differ).');
    }

    // If we stay on the same page due to a validation error, tweak username and try next again.
    setTimeout(() => {
      const err = qa('[role="alert"], .o6cuMc, .Ekjuhf').find((n) => n && (n.innerText || '').trim());
      if (err && q('input[name="Username"]')) {
        const ts2 = String(Date.now()).slice(-6);
        const username2 = `redhat.demo.${ts2}`;
        log('Validation message detected; retrying with', username2);
        setValue('input[name="Username"]', username2);
        setTimeout(() => clickNext(), 800);
      }
    }, 5000);
  };

  // Kick off.
  run();
})();
