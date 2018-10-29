require 'nokogiri'

module PkbHelper
    def all_notes
        @items.find_all("/notes/**/*.md").map do |note|
            match  = note.identifier.to_s.match(/^\/notes\/(.*)\.md$/)
            titles = match[1].split('/').map { |s| s.match(/^(\d+)-(.*)$/)[2] }
            digest = note.compiled_content.gsub(/<\/?[^>]*>/, "").slice(0..127)
            { :path => note.path, :titles => titles, :digest => digest }
        end
    end

    # todo: 遍历所有markdown，构建全局的目录结构，用来显示在网站左侧
    def site_map
        # 我们需要遵循用户指定的顺序，例如`02_系统`一定要排在第二位
        # ruby默认的hash是有序的，但我们还要处理用户指定的编号重复的情况
        all_notes.each do |note|
        end
    end

    # turn hashmap into html list
    def tree_to_list(toc)
        toc.to_s
    end

    # generate toc from content
    def note_toc(html)
        "fake toc"
    end
end

use_helper PkbHelper
