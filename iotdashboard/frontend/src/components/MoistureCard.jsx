import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer
} from "recharts"


function MoistureCard({ data }) {
    return (
        <div className="bg-gray-900 p-6 rounded-2xl w-72">
            <h2 className="text-xl mb-4">
                Moisture Chart
            </h2>

            <LineChart width={600} height={300} data={data}>

                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value"/>

            </LineChart>

            <ResponsiveContainer
                width="100%"
                height={300}
            >

            </ResponsiveContainer>
        </div>
    )
}

export default MoistureCard