var ElectionForm = function() {
    var self = this;

    self.reason = ko.observable();
    self.date_from = ko.observable();
    self.date_until = ko.observable();
    self.electionOptions = ko.observableArray();
    self.campusList = ko.observableArray();
    self.selectedCampus = ko.observable();

    self.addOption = function() {
        self.electionOptions.push({
            'name': '',
            'detail': ''
        });
    };

    self.removeOption = function() {
        self.electionOptions.remove(this);
    }

    self.sendNewElection = function () {
        $.ajax({
            url: '/sudo/elections/new',
            method: 'POST',
            contentType: 'application/json; charset=utf-8',
            headers: {
                'X-CSRF-Token': $('meta[name="csrf-token"]').attr('value')
            },
            data: ko.toJSON(self)
        }).done(function (res){
            alert('La elección se inscribió satisfactoriamente');
        }).fail(function (res){
            alert('No se pudo inscribir la elección. El formulario se encuentra incompleto o ocurrió un error en el servidor');
        });
    }

    $.get('/sudo/campuses/list').done(function(r) {
        self.campusList(r['campuses']);
    });

    $('input.datetime').datetimepicker({
        locale: 'es'
    });

    $('input[name="begindate"]').on('dp.change', function(e){
        self.date_from(e.date.format('YYYY-MM-DD HH:mm:ss'));
    });

    $('input[name="enddate"]').on('dp.change', function(e){
        $('input[name="begindate"]').data("DateTimePicker").maxDate(e.date);
        self.date_until(e.date.format('YYYY-MM-DD HH:mm:ss'));
    });
};

ko.applyBindings(new ElectionForm());