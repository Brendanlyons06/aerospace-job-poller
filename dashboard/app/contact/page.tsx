import PolicyShell from '../policy-shell';

export default function ContactPage() {
  return <PolicyShell eyebrow="Help and feedback" title="Contact AeroScout"><p>For a broken listing, missing company, feature suggestion, or general question, open an issue on the public GitHub project.</p><p><a className="policy-button" href="https://github.com/Brendanlyons06/aerospace-job-poller/issues" target="_blank" rel="noreferrer">Open the issue tracker ↗</a></p><h2>Protect your information</h2><p>GitHub issues are public. Do not include your email address, private subscription link, password, database key, or other personal information.</p><h2>Subscription help</h2><p>Every digest includes private links to manage preferences, unsubscribe, or permanently delete the subscription data. If a link no longer works, you can submit the email address again from the home page to request a new confirmation.</p></PolicyShell>;
}
