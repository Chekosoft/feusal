var VoteScreen = function() {
    var self = this;

    self.selectedOption = ko.observable(false);
    self.resultMessage = ko.observable();
    self.resultType = ko.observable();

    self.sendVote = function () {
        $.ajax({
            method: 'POST',
            data: ko.toJSON(self),
            contentType: 'application/json; charset=utf-8',
            headers: {
                'X-CSRF-Token': $('meta[name="csrf-token"]').attr('value')
            }
        }).done(function() {
            self.resultMessage('Voto contado con éxito');
            self.resultType('info');
        }).fail(function(response) {
            self.resultMessage("Ocurrió un error al colocar el voto: " + response.responseText);
            self.resultType('danger');
        });
    }
};

ko.applyBindings(new VoteScreen());