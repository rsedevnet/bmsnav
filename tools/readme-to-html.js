const pretty = require("pretty");
const { Octokit } = require("@octokit/core");

let token;
let out;

const tokenFlagIndex = process.argv.indexOf('-t');
const outFlagIndex = process.argv.indexOf('-o');

let validToken = false;
let validOut = false;

if (tokenFlagIndex > -1) {
  token = process.argv[tokenFlagIndex + 1];
  if (token?.trim?.().length) {
    validToken = true;
  }
}

if (!validToken) {
  console.error('Missing token.');
  process.exit(1);
}

if (outFlagIndex > -1) {
  out = process.argv[outFlagIndex + 1];
  if (out?.trim?.().length) {
    validOut = true;
  }
}

if (!validOut) {
  out = './README.html';
}

const main = async () => {
  const octokit = new Octokit({ auth: token });

  const response = await octokit.request('GET /repos/rsedevnet/bmsnav/readme', {
    owner: 'rsedevnet',
    repo: 'bmsnav',
    headers: {
      'Accept': 'application/vnd.github.html+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  });

  const html = pretty(response.data);

  console.log(html);
};

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
