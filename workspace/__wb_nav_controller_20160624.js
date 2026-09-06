var app = angular.module('getNav', ['ngRoute']);

app.controller('getNavController', function($scope, $http) {
	//allows for caching. hard to debug but easy to load!
	$.ajaxSetup({ cache: true });
	$http.get('/nav/nav.txt').then(function(data){
		$scope.nav = data;
    });
});
