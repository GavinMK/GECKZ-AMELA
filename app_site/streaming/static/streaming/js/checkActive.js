let id = location.pathname.split("/")[2];
document.getElementById(id).classList.add("active");
if(id === "inbox"){
    let id2 = location.pathname.split("/")[3];
    if(id2.includes("Inbox"))
        document.getElementById(id2).classList.add("active");
    else
        document.getElementById("unreadInbox").classList.add("active");
}