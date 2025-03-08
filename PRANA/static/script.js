let s_in=document.getElementById("in");
let s_up=document.getElementById("up");
let signup=document.getElementsByClassName("signup");
let signin=document.getElementsByClassName("signin");

s_in.addEventListener("click",function(){
  signup[0].classList.remove("d");
  this.style.borderLeft="4px solid #0f0776";
  s_up.style.borderLeft="";
  signin[0].classList.remove("c");
  signup[0].classList.toggle("c");
  
});

s_up.addEventListener("click",function(){
  signup[0].classList.remove("d");
  this.style.borderLeft="4px solid #0f0776";
  s_in.style.borderLeft="";
  signup[0].classList.remove("c");
  signin[0].classList.toggle("c");
  
});





// for(i=0;i<sign_in.length;i++){
//   sign_in[i].addEventListener("click",function(){

//   });
// }


