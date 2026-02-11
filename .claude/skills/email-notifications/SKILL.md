# Email Notifications

Production-ready email setup with Resend and NodeMailer.

## Resend (Recommended)

### Setup

```bash
npm install resend
```

### Basic Configuration

```typescript
// src/lib/email.ts
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendEmail({
  to,
  subject,
  html,
  text,
}: {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
}) {
  try {
    const { data, error } = await resend.emails.send({
      from: process.env.EMAIL_FROM || "noreply@yourdomain.com",
      to,
      subject,
      html,
      text,
    });

    if (error) {
      console.error("Email send error:", error);
      throw new Error(error.message);
    }

    return { success: true, id: data?.id };
  } catch (error) {
    console.error("Email failed:", error);
    throw error;
  }
}
```

### Environment Variables

```bash
# .env.local
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_FROM=notifications@yourdomain.com
```

### React Email Templates

```bash
npm install @react-email/components
```

```tsx
// src/emails/welcome.tsx
import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Link,
  Preview,
  Text,
} from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
  loginUrl: string;
}

export function WelcomeEmail({ name, loginUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to our platform!</Preview>
      <Body style={main}>
        <Container style={container}>
          <Heading style={h1}>Welcome, {name}!</Heading>
          <Text style={text}>
            Thank you for signing up. Click below to get started:
          </Text>
          <Link href={loginUrl} style={button}>
            Get Started
          </Link>
        </Container>
      </Body>
    </Html>
  );
}

const main = { backgroundColor: "#f6f9fc", padding: "40px 0" };
const container = { backgroundColor: "#ffffff", padding: "40px", borderRadius: "8px" };
const h1 = { color: "#1a1a1a", fontSize: "24px" };
const text = { color: "#4a4a4a", fontSize: "16px", lineHeight: "24px" };
const button = {
  backgroundColor: "#5e35b1",
  color: "#ffffff",
  padding: "12px 24px",
  borderRadius: "6px",
  textDecoration: "none",
  display: "inline-block",
};
```

### Using React Email with Resend

```typescript
import { render } from "@react-email/render";
import { WelcomeEmail } from "@/emails/welcome";

export async function sendWelcomeEmail(email: string, name: string) {
  const html = await render(WelcomeEmail({ name, loginUrl: "https://app.com/login" }));

  return sendEmail({
    to: email,
    subject: "Welcome to Our Platform!",
    html,
  });
}
```

---

## NodeMailer (Self-hosted/SMTP)

### Setup

```bash
npm install nodemailer
npm install -D @types/nodemailer
```

### Configuration

```typescript
// src/lib/nodemailer.ts
import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || "587"),
  secure: process.env.SMTP_SECURE === "true",
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

export async function sendEmail({
  to,
  subject,
  html,
  text,
}: {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
}) {
  try {
    const info = await transporter.sendMail({
      from: process.env.EMAIL_FROM,
      to: Array.isArray(to) ? to.join(", ") : to,
      subject,
      html,
      text,
    });

    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error("Email failed:", error);
    throw error;
  }
}
```

### Environment Variables (SMTP)

```bash
# Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# SendGrid
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key

# AWS SES
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-user
SMTP_PASS=your-ses-smtp-password
```

---

## Transactional Email Patterns

### Email Queue with Retry

```typescript
// src/lib/email-queue.ts
interface EmailJob {
  to: string;
  subject: string;
  html: string;
  retries: number;
  maxRetries: number;
}

const emailQueue: EmailJob[] = [];
const MAX_RETRIES = 3;
const RETRY_DELAY = 5000; // 5 seconds

export async function queueEmail(email: Omit<EmailJob, "retries" | "maxRetries">) {
  emailQueue.push({ ...email, retries: 0, maxRetries: MAX_RETRIES });
  processQueue();
}

async function processQueue() {
  while (emailQueue.length > 0) {
    const job = emailQueue.shift()!;

    try {
      await sendEmail(job);
      console.log(`Email sent to ${job.to}`);
    } catch (error) {
      if (job.retries < job.maxRetries) {
        job.retries++;
        console.log(`Retry ${job.retries}/${job.maxRetries} for ${job.to}`);
        await sleep(RETRY_DELAY * job.retries); // Exponential backoff
        emailQueue.push(job);
      } else {
        console.error(`Failed to send email to ${job.to} after ${job.maxRetries} retries`);
        // Log to error tracking service
      }
    }
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
```

### Batch Sending

```typescript
export async function sendBatchEmails(
  emails: Array<{ to: string; subject: string; html: string }>
) {
  const BATCH_SIZE = 10;
  const BATCH_DELAY = 1000; // 1 second between batches

  for (let i = 0; i < emails.length; i += BATCH_SIZE) {
    const batch = emails.slice(i, i + BATCH_SIZE);

    await Promise.allSettled(
      batch.map((email) => sendEmail(email))
    );

    if (i + BATCH_SIZE < emails.length) {
      await sleep(BATCH_DELAY);
    }
  }
}
```

---

## Email Template Best Practices

### 1. Inline CSS (Email clients strip `<style>` tags)

```tsx
// Bad
<div className="button">Click me</div>

// Good
<div style={{ backgroundColor: "#5e35b1", padding: "12px 24px" }}>Click me</div>
```

### 2. Use Tables for Layout

```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
      <table width="600" cellpadding="0" cellspacing="0">
        <!-- Content here -->
      </table>
    </td>
  </tr>
</table>
```

### 3. Always Include Plain Text

```typescript
await sendEmail({
  to: "user@example.com",
  subject: "Your Order",
  html: "<h1>Order Confirmed</h1><p>Details...</p>",
  text: "Order Confirmed\n\nDetails...", // Always include!
});
```

### 4. Keep Width Under 600px

```tsx
<Container style={{ maxWidth: "600px", margin: "0 auto" }}>
```

---

## Error Handling

```typescript
export async function sendEmailSafe(params: EmailParams): Promise<EmailResult> {
  try {
    const result = await sendEmail(params);
    return { success: true, ...result };
  } catch (error) {
    // Log to monitoring service
    console.error("Email error:", {
      to: params.to,
      subject: params.subject,
      error: error instanceof Error ? error.message : "Unknown error",
    });

    // Don't throw - return failure state
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to send email",
    };
  }
}
```

---

## Common Mistakes & Solutions

### 1. Gmail "Less Secure Apps" Blocked

**Fix:** Use App Passwords:
1. Enable 2FA on Google account
2. Generate App Password at myaccount.google.com
3. Use App Password as SMTP_PASS

### 2. Emails Going to Spam

**Fix:**
- Set up SPF, DKIM, DMARC records
- Use verified domain (not gmail.com)
- Include unsubscribe link
- Avoid spam trigger words

### 3. Rate Limiting

**Fix:** Implement queue with delays:
```typescript
// Resend: 10 emails/second on free tier
// SendGrid: Varies by plan
await sleep(100); // Between sends
```

### 4. HTML Rendering Issues

**Fix:** Test with [Litmus](https://litmus.com) or [Email on Acid](https://emailonacid.com)

---

## Production Checklist

- [ ] Domain verified with email provider
- [ ] SPF/DKIM/DMARC configured
- [ ] Unsubscribe mechanism implemented
- [ ] Plain text version included
- [ ] Error logging configured
- [ ] Retry logic implemented
- [ ] Rate limiting respected
- [ ] Templates tested across clients
- [ ] Bounce handling configured
- [ ] Analytics/tracking (optional)
