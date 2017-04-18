Markdown pipeline
=================

Uses the markdown rendering of github (for html code, not styling). In the future one would probably want to have a dedicated ruby daemon that parses a message queue and posts responses with the html.

from
https://gist.github.com/dalibor/892d907bf6b82284603c

```
require 'rubygems'
require 'bundler/setup'

require 'github/markup'
require 'html/pipeline'

file = ARGV[0]
abort("#{file} does not exist.") unless File.exists?(file)

html = GitHub::Markup.render(file)
pipeline = HTML::Pipeline.new [
  HTML::Pipeline::MarkdownFilter,
  HTML::Pipeline::SyntaxHighlightFilter
]

puts pipeline.call(html)[:output].to_s
```

```
source 'https://rubygems.org'

gem 'github-markup'
gem 'github-markdown'
gem 'github-linguist'
gem 'html-pipeline'
```