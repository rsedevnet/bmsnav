import fileinput
import os
import shutil
import sys
import gh_md_to_html

# gh-md-to-html -i -c -f file README.md -n index.html

html_out = os.path.join('docs', 'index.html')

try:
  gh_md_to_html.main('README.md', image_paths='', output_name=html_out)
except Exception as conversion_err:
  sys.stderr.write('\nError during conversion: ' + str(conversion_err) + '\n')
  sys.exit(1)
finally:
  try:
    shutil.rmtree('images')
    shutil.rmtree('github-markdown-css')
  except Exception as cleanup_err:
    sys.stderr.write('Error cleaning up after conversion: ' + str(cleanup_err) + '\n')
    sys.exit(1)

try:
  with fileinput.FileInput(html_out, inplace=True) as file:
    for line in file:
      print(line.replace('/github-markdown-css/github-css.css', 'style.css'), end='')

  with fileinput.FileInput(html_out, inplace=True) as file:
    for line in file:
      print(line.replace('user-content-', ''), end='')
except Exception as sr_err:
  sys.stderr.write('Error during CSS search/replace: ' + str(sr_err) + '\n') 
  sys.exit(1)

sys.exit(0)
