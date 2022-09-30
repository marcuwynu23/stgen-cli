import yaml,sys

HTML_TEMPLATE = '''<html lang="en">
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


def includes(template_dir,layout,name):
	str = ""
	for i in layout[name]['include']:
			str+=readhtmlfile(f"{template_dir}\{i}") + "\n"
	return str


def depstr(deps,name):
	str = ""
	for i in deps:
			if name == "scripts":
					str+= f'<script src="{i}" defer></script>'
			else:
					str+= f'<link rel="stylesheet" href="{i}">'
	return str

def handleConfig(config):
		deps = config["dependencies"]
		scripts = depstr(deps["scripts"],"scripts")
		styles = depstr(deps["styles"],"styles")
		return f"{styles}\n{scripts}\n{deps['html']}"


def configure(layoutfile,configData,compilehtmlfile):
		layout = readfile(layoutfile)
		layout = layout["layout"]
		template_dir = configData["template_dir"]
		
		

		header = includes(template_dir,layout,"header")
		main = includes(template_dir,layout,"main")
		footer = includes(template_dir,layout,"footer")
		layout_template = LAYOUT_TEMPLATE.format(header,main,footer)
		html_template = HTML_TEMPLATE.format(handleConfig(configData),configData["title"],layout_template)
		writefile(compilehtmlfile,html_template)
		

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
		f.write(data)
		return True
	return False

configData = readfile('./.gen/page.yml')
try:
	fileName = sys.argv[1]
except:
	fileName = "index.html"
configure("./.gen/layout.yml",configData,fileName)
