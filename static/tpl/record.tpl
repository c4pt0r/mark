<div class="record-item">
    <a href="<%= url %>" title="<%= url %>" target="_blank"><%= title %></a>
    <small><%= host %></small>
    <% _.each(tags, function(tag) { %> 
    	<span class="label label-primary"><%= tag %></span>
    <% }); %>
    <i class="fui-tag text-primary"></i>
    <i class="fui-export text-primary"></i>
    <i class="fui-cross-inverted text-primary"></i>
 </div>