document.addEventListener('DOMContentLoaded', (event) => {
    const today = new Date();
    const yyyy = today.getFullYear();
    let mm = today.getMonth() + 1; // getMonth() is zero-based
    let dd = today.getDate();

    // Add leading zeros to month and day if needed
    mm = mm < 10 ? '0' + mm : mm;
    dd = dd < 10 ? '0' + dd : dd;

    const formattedToday = `${yyyy}-${mm}-${dd}`;
    document.getElementById('date').value = formattedToday;
});