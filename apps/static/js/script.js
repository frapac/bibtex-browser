
function addHALEntry(id){
  console.log(id);
  var halEntry = document.getElementById("data" + id).innerText;
  var dataEntry = convertStringToJSON(halEntry);
  document.getElementById("bibtitle").value = dataEntry["title"];
  document.getElementById("bibyear").value = dataEntry["year"];
  document.getElementById("bibid").value = dataEntry["ID"];
  document.getElementById("bibauthor").value = dataEntry["author"];
  document.getElementById("bibtype").value = dataEntry["ENTRYTYPE"];
  document.getElementById("bibjournal").value = dataEntry["origin"];
  document.getElementById("bibkeyword").value = dataEntry["keywords"];
  document.getElementById("biburl").value = dataEntry["link"];

  modal.style.display = "block";
}

function convertStringToJSON(str){
  dataEntry = JSON.stringify(eval("(" + str + ")"));
  return JSON.parse(dataEntry);
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

document.onkeypress = function(evt) {
  evt = evt || window.event;
  var charCode = evt.keyCode || evt.which;
  if (evt.keyCode == 27) {
    modal.style.display = "none";
  }
};

var checkedyear = document.getElementsByClassName('checkyear');
var checkedtype = document.getElementsByClassName('checktype');
var checkedtags = document.getElementsByClassName('checktags');

// Get value of all checkbox checked in a specified array
function checkClickedTab(tab, field){
  var ss = field;
  var it, count;
  count = 0;
  for (it=0; it< tab.length; it++){
    if (tab[it].checked){
      ss = ss.concat(tab[it].value, ":");
      count += 1;
    };
  }

  if(count >= 1){
    return ss
  }
  else{
    return ""
  }
}


function checkClicked(){
  link = "/biblio/query?"
  cy = checkClickedTab(checkedyear, "year=");
  if(cy != ""){link = link.concat(cy, "&");}
  ct = checkClickedTab(checkedtype, "type=");
  if(ct != ""){link = link.concat(ct, "&");}
  ctags = checkClickedTab(checkedtags, "tags=");
  if(ctags != ""){link = link.concat(ctags, "&");}

  window.location.href = link
}

var it;
for (it=0; it < checkedyear.length; it++){
  checkedyear[it].onclick = checkClicked;
}
for (it=0; it< checkedtype.length; it++){
  checkedtype[it].onclick = checkClicked;
}
for (it=0; it< checkedtype.length; it++){
  checkedtags[it].onclick = checkClicked;
}
