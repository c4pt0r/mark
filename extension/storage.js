function storage( key, value ) {
  if ( typeof( value ) !== "undefined" ) {
    localStorage[ key ] = JSON.stringify( { "value": value } );
  } else {
    if ( typeof( localStorage[ key ] ) !== "undefined" ) {
      return JSON.parse( localStorage[ key ] ).value;
    } else {
      return undefined;
    }
  }
}
