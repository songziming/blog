site: theme
	mkdocs build

serve: theme
	mkdocs serve

theme:
	sass --style compressed source/main.scss writethedocs/css/main.css

deploy: site
	rsync -ru site/ szm@szm.me:~/blog/
