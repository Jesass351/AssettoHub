const addModalEl = document.getElementById('createModal');
addModalEl.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url; 
    console.log(form.action);
});