const createBookComp = document.getElementById('addModal');
createBookComp.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = document.getElementById('addForm');
    form.action = url; 
    let book_id = document.getElementById('book_id');
    book_id.value = event.relatedTarget.dataset.book_id
});