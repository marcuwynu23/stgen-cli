# stgen-cli
a commandline tool for generate static html file 

## How to generate html file
```python stgen-cli.py index.html```
### Prerequisite
	- PyYAML
	- .gen folder contains:
    - page.yml contains the page title,template folder directory, dependencies,etc
    - layout.yml contains the layout structure of the html files
	- template folder(you can name whatever you want) but you need to specify it in the page.yml in the .gen
  	- this template folder contains the html files that you will includes in the layout.html
 
# Project Structure
* project
 * .gen
   * layout.yml
   * page.yml
 * template
   * header
     * header.html
     * sidebar.html
   * main
     * content.html
   * footer
     * footer.html
 * compiled
   * index.html

# Contribute
