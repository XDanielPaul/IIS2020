
function validateInterpret(){
  console.log("GOT HERE");
  var name = document.forms["Interpret"]["interpret"].value;
  var members = document.forms["Interpret"]["members"].value;
  var rating = document.forms["Interpret"]["rating"].value;
  var genre = document.forms["Interpret"]["genre"].value;
  if(name == "" || members == "" || rating == "" || genre == ""){
    alert("Please fill all required fields!");
    return false;
  }

  rating = parseInt(rating);
  if(!Number.isInteger(rating) || rating <= 0 || rating > 10)
  {
    alert("Illegal value for rating!");
    document.getElementById("rating").value = "";
    return false;
  }

}


/**
 * Checking input types in /add_festival
 */
function validateForm() {
  // TODO: alert boxes with for example jQuery

  var name = document.forms["Form"]["name"].value;
  var genre = document.forms["Form"]["genre"].value;
  var date_start = document.forms["Form"]["date_start"].value;
  var date_end = document.forms["Form"]["date_end"].value;
  var location = document.forms["Form"]["location"].value;
  var price = document.forms["Form"]["price"].value;
  var max_capacity = document.forms["Form"]["max_capacity"].value;
  if(name == "" || genre == "" || date_start == "" ||  date_end == "" 
    || location == "" || price == "" || max_capacity == ""){
    alert("Please fill all required fields!");
    return false;
  }

  price = parseFloat(price);
  if(Number.isNaN(price) || price <= 0){
    alert("Illegal value for price!");
    document.getElementById("price").value = "";
    return false;
  }

  max_capacity = parseInt(max_capacity);
  if(!Number.isInteger(max_capacity) || max_capacity <= 0)
  {
    alert("Illegal value for max capacity!");
    document.getElementById("max_capacity").value = "";
    return false;
  }

  const start = new Date(date_start);
  const end = new Date(date_end);
  if(start > end){
    alert("Illegal date interval!");
    return false;
  }
}


function getDate() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; // January is 0
    var yyyy = today.getFullYear();
  
    if(dd < 10){
        dd = '0' + dd
    } 
  
    if(mm < 10){
        mm = '0' + mm
    } 
  
    today = yyyy + '-' + mm + '-' + dd;
    document.getElementById("date_start").min = today;
    document.getElementById("date_end").min = today;
  }
  
  window.onload = function() {
    getDate();
  };
