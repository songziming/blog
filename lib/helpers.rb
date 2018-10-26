
require 'nokogiri'

# [:path, :compiled_content, :reps, :parent, :children, :binary?, :raw_filename, :==, :[], :eql?, :inspect, :hash, :fetch, :key?, :attributes, :reference, :identifier, :raw_content, :_unwrap, :frozen?, :_context, :to_yaml, :to_yaml_properties, :psych_to_yaml, :instance_of?, :public_send, :instance_variable_get, :instance_variable_set, :instance_variable_defined?, :remove_instance_variable, :private_methods, :kind_of?, :instance_variables, :tap, :method, :public_method, :singleton_method, :is_a?, :extend, :define_singleton_method, :to_enum, :enum_for, :<=>, :===, :=~, :!~, :respond_to?, :freeze, :display, :object_id, :send, :to_s, :nil?, :class, :singleton_class, :clone, :dup, :itself, :taint, :tainted?, :untaint, :untrust, :trust, :untrusted?, :methods, :protected_methods, :public_methods, :singleton_methods, :!, :!=, :__send__, :equal?, :instance_eval, :instance_exec, :__id__]

module MyHelper
    def all_notes
        # @items.find_all("/notes/**/*.md").each do |note|
        #     match  = note.identifier.to_s.match(/^\/notes\/(.*)\.md$/)
        #     titles = match[1].split('/').map { |s| s.match(/^(\d+)-(.*)$/)[2] }
        #     p "item #{note.path.to_s} id #{note.identifier}"
        # end
        @items.find_all("/notes/**/*.md").map do |note|
            match  = note.identifier.to_s.match(/^\/notes\/(.*)\.md$/)
            titles = match[1].split('/').map { |s| s.match(/^(\d+)-(.*)$/)[2] }
            digest = note.compiled_content.gsub(/<\/?[^>]*>/, "").slice(0..127)
            { :path => note.path, :titles  => titles, :digest => digest }
        end
    end
end

use_helper MyHelper
