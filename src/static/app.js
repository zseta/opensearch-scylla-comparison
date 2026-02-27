function comparisonApp() {
  return {
    stuff: "hello",
    query: "",
    hasSearched: false,
    darkMode: true,
    databaseA: {
      latency: null,
      loading: false,
    },
    databaseB: {
      latency: null,
      loading: false,
    },
    queryIsEmpty() {
      isEmpty = this.query.trim() === "";
      //console.log(isEmpty);
      return isEmpty;
    },
  };
}
