#!/usr/bin/env ruby


use_helper Nanoc::Helpers::Blogging
use_helper Nanoc::Helpers::Rendering

module HierarchyHelper

    def levels(post)
        post.path.split("/").reject(&:empty?)
    end

    def categories(post)
        levels(post).slice(0..-2).map(&:capitalize).join("→")
    end

    def tags(post)
        post[:tags].map(&:downcase).join(" ")
    end

    def excerpt(post)
        post.compiled_content.gsub(/<\/?[^>]*>/, "").slice(0..127)
    end

    def hierarchy_obj
        h = {}
        sorted_articles.each do |post|
            path = levels(post)
            i = h
            path.slice(0..-2).each do |level|
                i[level] = {} if nil == i[level]
                i = i[level]
            end
            i[path[-1]] = "<a href=\"#{post.path}\">#{post[:title]}</a>"
        end
        h
    end

    def hierarchy_str(obj)
        str = "<ul>"
        obj.each do |k, v|
            str += "<li>"
            if Hash == v.class
                str += k + hierarchy_str(v)
            elsif String == v.class
                str += v
            end
            str += "</li>"
        end
        str += "</ul>"
        str
    end

    def hierarchy
        hierarchy_str(hierarchy_obj)
    end

end

use_helper HierarchyHelper