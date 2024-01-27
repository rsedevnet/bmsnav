const fs = require('fs');

if (!fs.existsSync('node_modules/rimraf')) {
  console.error("Couldn't find rimraf module (needed for clean). Did you forget to 'npm run install'?");
  process.exit(1);
}
