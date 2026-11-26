# Build the search index from the articles Jekyll rendered for one version.
require "json"
require "nokogiri"
require "pathname"

root = Pathname(ARGV.fetch(0))
entries = []
root.glob("**/*.html").sort.each do |file|
  document = Nokogiri::HTML(file.read)
  article = document.at_css("main article")
  next if !article || article.at_css("#search-page")

  url = file.relative_path_from(root).to_s.delete_suffix("index.html")
  title = url.empty? ? "Home" : article.at_css("h1")&.text&.strip
  next unless title
  mod = article.at_css('nav[aria-label="Module"] a')
  title = "#{mod.text.strip}.#{title}" if mod

  article.css("nav, script, style, template, svg, noscript").remove
  entry = {title: title, section: "", url: "./#{url}", text: +""}
  entries << entry
  article.xpath(".//h2[@id] | .//h3[@id] | .//h4[@id] | .//text()[normalize-space()]").each do |node|
    if node.element?
      entry = {title: title, section: node.text.strip, url: "./#{url}##{node['id']}", text: +""}
      entries << entry
    else
      entry[:text] << node.text << " "
    end
  end
end
entries.each { |entry| entry[:text] = entry[:text].split.join(" ") }
root.join("search-index.json").write(JSON.generate(entries))
