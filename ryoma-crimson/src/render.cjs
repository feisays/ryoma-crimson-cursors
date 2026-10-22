const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  for (const job of jobs) {
    await sharp(Buffer.from(job.svg)).resize(job.size, job.size).png().toFile(job.output);
  }
})().catch(e => { console.error(e); process.exit(1); });
