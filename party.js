// Birthday-party decorations: side balloons on big screens, and a confetti burst when the final podium
// or a "答對" screen appears. Purely visual; it never touches the game state.
(()=>{
  const COLORS=["#ff4f7b","#ffd23f","#12b5a6","#8b4dff","#ff8a1f","#2f7cf6","#2ee6d6"];
  const reduce=matchMedia("(prefers-reduced-motion:reduce)").matches;
  function balloons(){
    const box=document.createElement("div");box.className="pg-balloons";box.setAttribute("aria-hidden","true");
    const spots=[2,7,12,88,93,97];
    spots.forEach((x,i)=>{const b=document.createElement("span");b.className="pg-balloon";
      b.style.left=x+"%";b.style.setProperty("--bc",COLORS[i%COLORS.length]);
      b.style.setProperty("--dur",(12+i*1.7)+"s");b.style.setProperty("--del",(-i*2.3)+"s");
      b.style.transform="scale("+(0.8+(i%3)*0.15)+")";box.appendChild(b)});
    document.body.prepend(box);
  }
  let last=0;
  function confetti(n){
    if(reduce||Date.now()-last<2500)return;last=Date.now();
    const box=document.createElement("div");box.className="pg-confetti";box.setAttribute("aria-hidden","true");
    for(let i=0;i<n;i++){const c=document.createElement("i");
      c.style.left=Math.random()*100+"%";c.style.background=COLORS[i%COLORS.length];
      if(i%3===0)c.style.borderRadius="50%";
      c.style.setProperty("--dx",(Math.random()*160-80)+"px");c.style.setProperty("--rot",(360+Math.random()*900)+"deg");
      c.style.setProperty("--dur",(2.2+Math.random()*1.8)+"s");c.style.setProperty("--del",(Math.random()*.6)+"s");
      box.appendChild(c)}
    document.body.appendChild(box);setTimeout(()=>box.remove(),5000);
  }
  window.partyConfetti=confetti;
  function watch(){
    const seen=new WeakSet();
    new MutationObserver(()=>{
      const p=document.querySelector(".podium,.status.good");
      if(p&&!seen.has(p)){seen.add(p);confetti(p.classList.contains("podium")?140:60)}
    }).observe(document.body,{childList:true,subtree:true});
  }
  const go=()=>{balloons();watch()};
  document.readyState==="loading"?document.addEventListener("DOMContentLoaded",go):go();
})();
