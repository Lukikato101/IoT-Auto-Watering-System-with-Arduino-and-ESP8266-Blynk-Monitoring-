import { useEffect, useState } from "react"
import MoistureCard from "./components/MoistureCard"
import StatusCard from "./components/cards/statusCard"
import useSensorData from "./hooks/useSensorData"

function App() {

  const {
    moisture,
    history,
    loading
  } = useSensorData()

  const pumpStatus =
    moisture < 40
      ? "ON"
      : "OFF"

  if (loading) {
    return (
      <div className="
        bg-black
        min-h-screen
        text-white
        flex
        items-center
        justify-center
      ">
        <h1 className="text-4xl">
          Loading...
        </h1>
      </div>
    )
  }

  return (
    <div className="bg-black min-h-screen text-white p-10">

      <h1 className="
        text-4xl
        font-bold
        mb-10
      ">
        IoT Dashboard
      </h1>

      <div className="
        grid
        grid-cols-1
        md:grid-cols-2
        gap-6
      ">

        <StatusCard 
          title="Soil Moisture"
          value={`${moisture}`}
          color="text-green-400"
        />

        <StatusCard
          title="Pump Status"
          value={pumpStatus}
          color={
            pumpStatus === "ON"
              ? "text-blue-400"
              : "text-red-400"
          }
        />

      </div>

      

    </div>
  )
}

export default App