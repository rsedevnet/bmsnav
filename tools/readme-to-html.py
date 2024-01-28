import fileinput
import os
import shutil
import sys
import gh_md_to_html

# gh-md-to-html -i -c -f file README.md -n index.html

html_out = os.path.join('docs', 'index.html')

# Use the gd_md_to_html lib to convert markdown to html.
try:
  gh_md_to_html.main('README.md', image_paths='', output_name=html_out)
except Exception as conversion_err:
  sys.stderr.write('\nError during conversion: ' + str(conversion_err) + '\n')
  sys.exit(1)
finally:
  # Remove directories created by gd_md_to_html.
  try:
    shutil.rmtree('images')
    shutil.rmtree('github-markdown-css')
  except Exception as cleanup_err:
    sys.stderr.write('Error cleaning up after conversion: ' + str(cleanup_err) + '\n')
    sys.exit(1)

# Replace and insert various things.
try:
  # I know this isn't efficient, but the file is small.
  with fileinput.FileInput(html_out, inplace=True) as file:
    for line in file:
      print(line.replace('/github-markdown-css/github-css.css', 'style.css'), end='')

  with fileinput.FileInput(html_out, inplace=True) as file:
    for line in file:
      print(line.replace('user-content-', ''), end='')

  with open(html_out, 'r+') as file:
    contents = file.readlines()
    contents.insert(3, '<title>BMSNav</title>\n')
    file.seek(0)
    file.writelines(contents)

except Exception as sr_err:
  sys.stderr.write('Error during CSS search/replace: ' + str(sr_err) + '\n') 
  sys.exit(1)
