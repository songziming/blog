require 'nokogiri'

# [:path, :compiled_content, :reps, :parent, :children, :binary?, :raw_filename, :==, :[], :eql?, :inspect, :hash, :fetch, :key?, :attributes, :reference, :identifier, :raw_content, :_unwrap, :frozen?, :_context, :to_yaml, :to_yaml_properties, :psych_to_yaml, :instance_of?, :public_send, :instance_variable_get, :instance_variable_set, :instance_variable_defined?, :remove_instance_variable, :private_methods, :kind_of?, :instance_variables, :tap, :method, :public_method, :singleton_method, :is_a?, :extend, :define_singleton_method, :to_enum, :enum_for, :<=>, :===, :=~, :!~, :respond_to?, :freeze, :display, :object_id, :send, :to_s, :nil?, :class, :singleton_class, :clone, :dup, :itself, :taint, :tainted?, :untaint, :untrust, :trust, :untrusted?, :methods, :protected_methods, :public_methods, :singleton_methods, :!, :!=, :__send__, :equal?, :instance_eval, :instance_exec, :__id__]

module PkbHelper
    # generate digest
    def digest(note)
        note.compiled_content.gsub(/<\/?[^>]*>/, '').slice(0..127)
    end

    # generate toc from content
    def note_toc(html)
        doc = Nokogiri::HTML::DocumentFragment.parse(html)
        sel = (3..6).map(&-> (x) { "h#{x}[@id]" }).join('|')
        hdr = doc.xpath(sel)
        return if hdr.empty?
        toc = ''
        base  = hdr.map(&-> (h) { h.name.slice(1..-1).to_i }).min.to_i
        level = base
        hdr.each do |h|
            l = h.name.slice(1..-1).to_i
            if l > level
                toc += '<ul>'  * (l - level)
            elsif level > l
                toc += '</ul>' * (level - l)
            end
            toc += "<li><a href=\"##{h[:id]}\">#{h.children}</a></li>"
            level = l
        end
        if level > base
            toc += '</ul>' * (level - base)
        end
        '<ul>' + toc + '</ul>'
    end
end

use_helper PkbHelper
use_helper Nanoc::Helpers::Rendering
