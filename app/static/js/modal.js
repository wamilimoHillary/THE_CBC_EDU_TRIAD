// static/js/modal.js
document.addEventListener('DOMContentLoaded', function () {
    // Get all "Add" buttons
    const addButtons = document.querySelectorAll('.btn-add');
    const overlay = document.getElementById('overlay');

    // Add event listeners to all "Add" buttons
    addButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            // Get the modal ID from the button's data-modal attribute
            const modalId = button.getAttribute('data-modal');
            const modal = document.getElementById(modalId);

            // Show the modal and overlay
            if (modal) {
                modal.style.display = 'block';
                overlay.style.display = 'block';
            }
        });
    });

    // Close modal when the close button is clicked
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                overlay.style.display = 'none';
            }
        });
    });

    // Close modal when the overlay is clicked
    overlay.addEventListener('click', () => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        overlay.style.display = 'none';
    });
});



document.addEventListener('DOMContentLoaded', function () {
    // Existing modal logic...

    // Add event listeners for Edit buttons
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const modalId = button.getAttribute('data-modal');
            const modal = document.getElementById(modalId);

            if (modal) {
                const teacherId = button.getAttribute('data-teacher-id');
                fetchTeacherDetails(teacherId, modal);
                modal.style.display = 'block';
                overlay.style.display = 'block';
            }
        });
    });
   


    // Function to fetch teacher details for editing
    function fetchTeacherDetails(teacherId, modal) {
        fetch(`/admin/get_teacher/${teacherId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('edit-teacher-id').value = data.UserID;
                document.getElementById('edit-first-name').value = data.FirstName;
                document.getElementById('edit-last-name').value = data.LastName;
                document.getElementById('edit-email').value = data.Email;
                document.getElementById('edit-phone').value = data.Phone;
                document.getElementById('edit-hire-date').value = data.HireDate;
                document.getElementById('edit-is-active').value = data.is_active; // Set dropdown value
            })
            .catch(error => console.error('Error fetching teacher details:', error));
    }
});


document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners for Delete buttons in the table
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const modalId = button.getAttribute('data-modal');
            console.log('Modal ID from button:', modalId); // Debugging
            const modal = document.getElementById(modalId);

            if (modal) {
                const teacherId = button.getAttribute('data-teacher-id');
                console.log('Delete button clicked. Teacher ID:', teacherId); // Debugging
                document.getElementById('delete-teacher-id').value = teacherId; // Set teacher ID in hidden input
                modal.style.display = 'block';
                overlay.style.display = 'block';
            } else {
                console.error('Modal not found:', modalId); // Debugging
            }
        });
    });

    // Close modal when Cancel button is clicked
    const cancelButtons = document.querySelectorAll('.btn-cancel');
    cancelButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                overlay.style.display = 'none';
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('overlay');

    // Add event listeners for Edit buttons
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const modalId = button.getAttribute('data-modal');
            const modal = document.getElementById(modalId);

            if (modal) {
                const studentId = button.getAttribute('data-student-id');
                fetchStudentDetails(studentId, modal);
                modal.style.display = 'block';
                overlay.style.display = 'block';
            }
        });
    });

    // Add event listeners for Delete buttons
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();

            const modalId = button.getAttribute('data-modal');
            const modal = document.getElementById(modalId);

            if (modal) {
                const studentId = button.getAttribute('data-student-id');
                document.getElementById('delete-student-id').value = studentId;
                modal.style.display = 'block';
                overlay.style.display = 'block';
            }
        });
    });

    // Close modal when Cancel button is clicked
    const cancelButtons = document.querySelectorAll('.btn-cancel');
    cancelButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                overlay.style.display = 'none';
            }
        });
    });

    // Function to fetch student details for editing
    function fetchStudentDetails(studentId, modal) {
        fetch(`/admin/get_student/${studentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                // Populate the form fields with the fetched data
                document.getElementById('edit-student-id').value = data.UserID;
                document.getElementById('edit-first-name').value = data.FirstName;
                document.getElementById('edit-last-name').value = data.LastName;
                document.getElementById('edit-email').value = data.Email;
                document.getElementById('edit-phone').value = data.Phone;
                document.getElementById('edit-student-number').value = data.StudentNumber;
                document.getElementById('edit-registration-date').value = data.RegistrationDate;
                document.getElementById('edit-is-active').value = data.is_active; // Set dropdown value
            })
            .catch(error => console.error('Error fetching student details:', error));
    }
});





















// JavaScript to toggle Advanced Filters
document.getElementById('advanced-search-toggle').addEventListener('click', function () {
    const advancedFilters = document.getElementById('advanced-filters');
    if (advancedFilters.style.display === 'none') {
        advancedFilters.style.display = 'flex';
        this.textContent = 'Hide Advanced Filters';
    } else {
        advancedFilters.style.display = 'none';
        this.textContent = 'Advanced Filters';
    }
});
