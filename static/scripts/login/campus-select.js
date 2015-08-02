var CampusSelect = function() {
    var self = this;

    self.campusList = ko.observableArray();
    self.selectedCampus = ko.observable();

    self.sendCampus = function() {
        $.ajax({
            method: 'POST',
            url: '/login/set_campus',
            data: ko.toJSON(self),
            contentType: 'application/json; charset=utf-8',
            headers: {
                'X-CSRF-Token': $('meta[name="csrf-token"]').attr('value')
            }
        }).done(function (){
            alert('Campus seleccionado.');
            window.location.replace('/');
        }).fail(function() {
            alert('Ocurrió un error al configurar el campus. Intenta de nuevo');
        });
    };

    $.get('/login/get_campus_list').done(function(r){
        self.campusList(r['campuses']);
    });

};

ko.applyBindings(new CampusSelect());