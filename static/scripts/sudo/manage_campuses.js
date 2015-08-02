var CampusManagement = function() {

    var self = this;
    self.campusList = ko.observableArray();
    self.isLoaded = ko.observable(false);

    self.hasChanged = ko.computed(function() {
        return !(_.isEmpty(_.xor(self.campusList(), self.originalList)));
    });

    self.originalList = [];

    self.addCampus = function() {
        self.campusList.push({name: ''});
    };

    self.removeCampus = function() {
        self.campusList.remove(this);
    };

    self.restoreCampuses = function() {
        self.campusList(_.clone(self.originalList));
    };

    self.sendChanges = function() {
        $.ajax({
            method: 'POST',
            url: '/sudo/campuses',
            contentType: 'application/json; charset=utf-8',
            headers: {
                'X-CSRF-Token': $('meta[name="csrf-token"]').attr('value')
            },
            data: ko.toJSON({
                campuses: _.map(self.campusList(), 'name')
            })
        }).done(function(response) {
            self.originalList = _.clone(self.campusList());
            self.campusList.valueHasMutated();
            alert('Lista de campus cambiada con éxito');
        }).fail(function(response){
            alert('Ocurrió un problema al cambiar los campus. Intente de nuevo.');
        });
    };

    $.get('/sudo/campuses/list').done(function (r) {
        var list = _.map(r['campuses'], function(n) {
            return { name: n['pretty'] };
        });
        self.originalList = _.clone(list);
        self.campusList(_.clone(list));
        self.isLoaded(true);
    });
};

ko.applyBindings(new CampusManagement());