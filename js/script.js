
document.addEventListener('DOMContentLoaded', function () {

	// On click on any .section-title, get the parent's ID and move to the location's hash
	var sectionTitles = document.querySelectorAll('.section-title');
	sectionTitles.forEach(function (sectionTitle) {
		sectionTitle.addEventListener('click', function () {
			let sectionId = this.parentElement.id;
			let titleID = this.id;
			if (sectionId) window.location.hash = sectionId;
			else if (titleID) window.location.hash = titleID;
			else window.location.hash = '';
		});
	});

});