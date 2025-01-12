const Home = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-6" role="heading">
          Welcome to OptiHealth
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          A portmanteau of "Optimal" and "Health", OptiHealth is a workout planner that caters specifically towards your own body.
        </p>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Get Started</h2>
          <p className="text-gray-600 mb-6">
            Fill out our form to receive a customized workout split tailored to your needs.
          </p>
          <a
            href="/form"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            role="button"
          >
            Create Your Plan
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;
