_store = []

function pega_elementos(store=_store){

	regex = /^Plantão +(Azul|Verde|Branco|Vermelho|Brasil) +-? \d{2}\/\d{2}/gi
	regex2 = /Pacientes internados/gi
	try{
		text = document.querySelector("#x_divtagdefaultwrapper").innerText
	}
	catch(e){
		console.log("Erou")
	}

	proximo_item()	
	match1 = text.match(regex)
	match2 = text.match(regex2)
	if (match1 || match2){
		store.push(text)
        console.log("Adicionado : " + match1)
		return true
	}

	return false

}

function proximo_item(){

	item = document.querySelector("._lvv_L1");
	item.classList.toggle("_lvv_L1");
	item.click()

	//Aguarda um tempo até pegar o próximo item
	setTimeout(pega_elementos,1500)

}