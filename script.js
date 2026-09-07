document.addEventListener("DOMContentLoaded", function () {

    const deleteButtons = document.querySelectorAll(
        'form[action^="/delete_task"] button'
    );

    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to delete this task?")) {
                event.preventDefault();
            }
        });
    });

});
