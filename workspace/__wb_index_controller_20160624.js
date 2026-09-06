var qs=function(e){if(e=="")return{};var t={};for(var n=0;n<e.length;++n){var r=e[n].split("=");if(r.length!=2)continue;t[r[0]]=decodeURIComponent(r[1].replace(/\+/g," "))}return t}(window.location.search.substr(1).split("&"))

var app = angular.module('getIndex', ['getNav', 'ngRoute']); 

app.controller('getIndexController', function($scope, $http) {
    $scope.isActive = function (viewLocation) {
        var active = (viewLocation === $location.path());
        return active;
    };
	$http.get("backend.php").success(function(data){
		$scope.data = data;
		console.log(data.topics);
		graphPublications(data.topics);	
	});	
});
