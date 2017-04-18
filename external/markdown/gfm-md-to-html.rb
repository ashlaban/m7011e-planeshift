#! /usr/bin/env ruby
require 'github/markup'

filename = ARGV[0]
abort("#{filename} does not exist.") unless File.exists?(filename)

html = GitHub::Markup.render(filename, File.read(filename))
puts html.to_s