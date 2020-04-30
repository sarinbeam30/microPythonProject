require('dotenv').config();
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// MQTT_SETUP
const mqtt = require('mqtt');
const mqtt_client = mqtt.connect('mqtt://hairdresser.cloudmqtt.com', {
  username: 'odbyktmn',  // Username ที่สร้าง
  password: '9esnfcLYs5wF',  // Password ที่สร้าง
  port: 17758 // Port ที่ได้จากหน้า Dashboard
});

var mqtt_json_information;

// postgreSQL_SETUP
const {Pool, Client} = require('pg');
const query = `SELECT * FROM data_logger`;
const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "mqtt_database",
  password: "Bless45315",
  port: "5432"
});

const postgresql_client = new Client({
  user: "postgres",
  host: "localhost",
  database: "mqtt_database",
  password: "Bless45315",
  port: "5432"
})

postgresql_client.connect()
console.log('DB is connected')

// pool.query(query, (err, res) => {
//   console.log(err, res)
//   pool.end()
// })

// postgresql_client.query(query, (err, res) => {
//   if (err) {
//       console.error(err);
//       return;
//   }
//   console.log('Table is successfully created');
//   postgresql_client.end();
// });

function add_to_database(mqtt_data){
  const text = 'INSERT INTO data_logger (SENSOR, WATER_LEVEL, LONGTITUDE, LATITUDE, DATE_AND_TIME) VALUES($1, $2, $3, $4, $5)';
  const value = [mqtt_data['#SENSOR'], mqtt_data['VALUE'], mqtt_data['LONGITUDE'], mqtt_data['LATITUDE'], mqtt_data['DATE_AND_TIME']];

  // pool.query(text, value, (err, res) => {
  //   console.log(err, res)
  //   // pool.end()
  // })

  postgresql_client.query(text, value, (err, res) => {
    if (err) {
        console.error(err);
        return;
    }
    console.log('Table is added successfully\n');
    // postgresql_client.end();
  });

}


mqtt_client.on('connect', function() { // When connected
  console.log("Connected to CloudMQTT");
  
  // Subscribe to the id_of_sensor
  mqtt_client.subscribe('/BOARD_1', function() {
    // when a message arrives, do something with it
    mqtt_client.on('message', function(topic, message, packet) {
      console.log(topic + " : " + message);
      mqtt_json_information = JSON.parse(message);
      add_to_database(mqtt_json_information);

    });
  });
});


app.listen(port, () => console.log(`Example app listening on port ${port}!`));