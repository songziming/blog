#!/usr/bin/env ruby

require 'nokogiri'

use_helper Nanoc::Helpers::Blogging
use_helper Nanoc::Helpers::Rendering
# use_helper Nanoc::Helpers::Tagging
# use_helper Nanoc::Helpers::LinkTo

# 我们定义了自己的 helper，用来生成文章的分类和目录
# 文章都放在 posts 目录下，如果还有子目录，那子目录的名称就是文章分类
# 我们不仅需要给每一篇文章确定它的分类，还需要知道每一个分类之下有哪些文章，这就需要从全局文章列表开始分析

# 另外还有目录，一篇文章的目录可以由 Kramdown 直接生成，但我们希望将目录显示在左侧列表，就像 readthedocs 一样。
# 因此，我们使用 Nokogiri 直接分析 HTML，提取里面的内容生成目录

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
        @items.find_all("/posts/**/*.md").each do |post|
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

    # 分析 Kramdown 生成的 HTML，提取并生成文章的目录
    # 必须开启 kramdown 的 auto_ids 选项
    def toc(html)
        doc = Nokogiri::HTML::DocumentFragment.parse(html)
        sel = (3..6).map(&-> (x) { "h#{x}[@id]" }).join("|")
        hdr = doc.xpath(sel)
        return if hdr.empty?
        toc = ""
        base  = hdr.map(&-> (h) { h.name.slice(1..-1).to_i }).min.to_i
        level = base
        hdr.each do |h|
            l = h.name.slice(1..-1).to_i
            if l > level
                toc += "<ul>"  * (l - level)
            elsif level > l
                toc += "</ul>" * (level - l)
            end
            toc += "<li><p><a href=\"##{h[:id]}\">#{h.children}</a></p></li>"
            level = l
        end
        if level > base
            toc += "</ul>" * (level - base)
        end
        toc
    end

end

use_helper HierarchyHelper