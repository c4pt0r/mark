
$(document).ready(function(){
  var url = "";
  var title = "";
  var token = storage("token");
  var record_id = null;
  if (token === undefined) {
    location.href="./login.html"
  }
  console.log('token ' + token)
  chrome.tabs.getSelected(null,function(tab) {
      url = tab.url;
      $("#title").val(tab.title);
      $.post("http://localhost:5000/record/add", {token:token, title:tab.title, url:url}, function(d) {
        var ret = JSON.parse(d)
        if (ret.ret == 0) {
          $("#info").html("Mark Success!");
          record_id = ret.id;
          $("#tags").val(ret.tags)
        } else {
          $("#info").html("<font color='red'>Error: "+ ret.msg +"</font>");
        }
      })
  });

  $('#update-btn').click(function(){
      var title = $("#title").val();
      var tags = $('#tags').val();
      console.log(url + ' ' + title + ' ' + tags)
      $.post("http://localhost:5000/record/update", {id:record_id, token:token, title:title, tags:tags}, function(d) {
        var ret = JSON.parse(d)
        if (ret.ret == 0) {
          $("#info").html("Update Success");
        }
      }) 
  });

})