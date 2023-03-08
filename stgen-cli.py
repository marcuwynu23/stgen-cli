import yaml,sys,os
from bs4 import BeautifulSoup


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	{0}
	<title>{1}</title>
</head>
<body>
{2}
</body>
</html>
'''

LAYOUT_TEMPLATE = '{0}\n{1}\n{2}'
INCLUDES_DIR = "./includes"

# beautify html code function
def beautify_html(html_data):
	return BeautifulSoup(html_data, 'html.parser').prettify()

def readhtmlfile(filename):
	data = None
	with open(filename, 'r') as f:
		data = f.read()
	return data

def readfile(filename):
	data = None
	with open(filename, 'r') as f:
		data = yaml.safe_load(f)
	return data

def writefile(filename, data):
	with open(filename, 'w') as f:
		beautify_html_data = beautify_html(data)
		f.write(beautify_html_data)
		return True
	return False


def includes(includes_dir,layout,name):
	str = ""
	for i in layout[name]['include']:
			str+=readhtmlfile(f"{includes_dir}\{i}") + "\n"
	return str


def depstr(deps,name):
	str = ""
	for i in deps:
			if name == "scripts":
					str+= f'<script src="{i}" defer></script>'
			else:
					str+= f'<link rel="stylesheet" href="{i}">'
	return str


def get_all_files_names(directory):
		file_names = []
		for  root,directories,files in os.walk(directory):
				for filename in files:
						file_names.append(filename)
		return file_names

def handleConfig(config):
		deps = config["dependencies"]
		scripts = depstr(deps["scripts"],"scripts")
		styles = depstr(deps["styles"],"styles")
		return f"{styles}\n{scripts}\n{deps['html']}"




def configure(layoutfile,configData,compilehtmlfile):
		layout = readfile(layoutfile)
		layout = layout["layout"]
		template_dir = configData["template_dir"]
		
		

		header = includes(INCLUDES_DIR,layout,"header")
		main = get_main_content(template_dir,compilehtmlfile)
		footer = includes(INCLUDES_DIR,layout,"footer")
		layout_template = LAYOUT_TEMPLATE.format(header,main,footer)
		html_template = HTML_TEMPLATE.format(handleConfig(configData),configData["title"],layout_template)
		writefile(f'compiled\{compilehtmlfile}.html',html_template)
		
def get_main_content(template_dir,compilehtmlfile):
		html_fragment_content = readhtmlfile(f"{template_dir}\{compilehtmlfile}.stg")

		return """
		<main>
		{0}
		</main>
		""".format(html_fragment_content)


def main(file):
	configData = readfile('./.gen/page.yml')
	configure("./.gen/layout.yml",configData,file)


if __name__ == "__main__":
	files = get_all_files_names("./templates")
	for file in files:
			file = file.split(".")[0]
			main(file)

