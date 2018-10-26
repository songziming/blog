require 'nokogiri'

module MyHelper
    def all_notes
        @items.find_all("/notes/**/*.md").map do |note|
            match  = note.identifier.to_s.match(/^\/notes\/(.*)\.md$/)
            titles = match[1].split('/').map { |s| s.match(/^(\d+)-(.*)$/)[2] }
            digest = note.compiled_content.gsub(/<\/?[^>]*>/, "").slice(0..127)
            { :path => note.path, :titles  => titles, :digest => digest }
        end
    end
end

use_helper MyHelper
