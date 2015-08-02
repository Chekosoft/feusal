var ElectionList = function() {
    var self = this;
    self.elections = ko.observableArray();
    self.currentPage = ko.observable(0);
    self.canLoadMore = ko.observable(false);
    self.noResults = ko.observable(false);

    self.getElections = function() {
        $.get('/elections/list', {
            page: self.currentPage()
        }).done(function(response){
            if(response['elections'].length > 0) {
                self.elections(response['elections']);
                self.canLoadMore(self.elections().length == 20);
            }
            else {
                self.noResults = true;
            }
        });
    }

    self.getMoreElections = function() {
        self.currentPage(self.currentPage() + 1);
        self.getElections();
    }

    $(function() {
        self.getElections();
    });
};

ko.applyBindings(new ElectionList());