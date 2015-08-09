var ElectionList = function() {
    var self = this;
    self.elections = ko.observableArray();
    self.currentPage = ko.observable(0);
    self.canLoadMore = ko.observable(false);
    self.isLoading = ko.observable(false);

    self.getElections = function() {
        self.isLoading(true);
        $.get('/elections/list', {
            page: self.currentPage()
        }).done(function(response){
            self.isLoading(false);
            if(response['elections'].length > 0) {
                self.elections(response['elections']);
                self.canLoadMore(self.elections().length == 20);
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
